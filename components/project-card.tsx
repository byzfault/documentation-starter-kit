import React from 'react'
import styles from './project-card.module.css'

/**
 * Project card for /portfolio.
 *
 * Status is the only switch that matters. A card shows a demo link when, and
 * only when, `status` is "live" and a `url` is supplied, so nothing on the page
 * can imply a deployment that does not exist yet. Shipping a project is a
 * one-line edit at the call site:
 *
 *   status="build"                     ->  status="live" url="https://..."
 */

type Status = 'build' | 'live' | 'case-study'

const STATUS_LABEL: Record<Status, string> = {
  build: 'In build',
  live: 'Live',
  'case-study': 'Case study',
}

const STATUS_CLASS: Record<Status, string> = {
  build: styles.statusBuild,
  live: styles.statusLive,
  'case-study': styles.statusCase,
}

export interface ProjectCardProps {
  title: string
  status: Status
  /** Public URL. Required for the demo link to render at all. */
  url?: string
  /** Text for the demo link. Defaults to "Open it". */
  urlLabel?: string
  /** Public repository. */
  repo?: string
  /** One line under the title: what it is, or the engagement and dates. */
  kicker?: string
  problem: React.ReactNode
  approach: React.ReactNode
  stack?: string[]
  /** Internal link to a longer write-up. */
  readMore?: { href: string; label: string }
}

export function ProjectCard({
  title,
  status,
  url,
  urlLabel = 'Open it',
  repo,
  kicker,
  problem,
  approach,
  stack,
  readMore,
}: ProjectCardProps) {
  const isLive = status === 'live' && Boolean(url)

  return (
    <article className={styles.card}>
      <div className={styles.head}>
        <h3 className={styles.title}>{title}</h3>
        <span className={`${styles.status} ${STATUS_CLASS[status]}`}>
          {STATUS_LABEL[status]}
        </span>
      </div>

      {kicker ? <p className={styles.kicker}>{kicker}</p> : null}

      <div className={styles.body}>
        <p className={styles.label}>Problem</p>
        <p className={styles.text}>{problem}</p>

        <p className={styles.label}>Approach</p>
        <p className={styles.text}>{approach}</p>

        {stack?.length ? (
          <ul className={styles.stack}>
            {stack.map(item => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        ) : null}
      </div>

      <div className={styles.links}>
        {isLive ? (
          <a className={styles.link} href={url} target="_blank" rel="noreferrer">
            {urlLabel}
          </a>
        ) : null}

        {repo ? (
          <a className={styles.link} href={repo} target="_blank" rel="noreferrer">
            Source on GitHub
          </a>
        ) : null}

        {readMore ? (
          <a className={styles.link} href={readMore.href}>
            {readMore.label}
          </a>
        ) : null}

        {status === 'build' ? (
          <span className={styles.pending}>No public demo yet</span>
        ) : null}
      </div>
    </article>
  )
}

export function ProjectGrid({ children }: { children: React.ReactNode }) {
  return <div className={styles.grid}>{children}</div>
}

export default ProjectCard
